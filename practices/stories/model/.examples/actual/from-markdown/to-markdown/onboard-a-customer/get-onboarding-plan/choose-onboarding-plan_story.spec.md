## Story: Choose Onboarding Plan

### Scenario Outline: Choose Onboarding Plan

### Background

*Given* the Prospect is in Account Setup
*And* the Prospect has a ++My Paradise customer++ with a ++Mavenir shopping cart++
*But* no ++plan++ is in the ++Mavenir shopping cart++
*And* Keep current plan is not shown
*When* the Prospect is forwarded to Plan Selection
*Then* the system retrieves the ++plan++ catalog from the Midtier
*And* the Prospect sees ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, and ++plan++ ++Atlas++
*And* each ++plan++ has a Select operation
*When* the Prospect clicks Select on ++plan++ ++{scenario}++
*Then* the system patches the ++Mavenir shopping cart++ with ++{scenario}++ through the Midtier
*And* the ++My Paradise customer++ cart is updated in session with ++{scenario}++
*And* the Prospect is forwarded to Time to pick your number


### Scenario: Choose a different ++plan++

### Background

*Given* the Prospect is in Account Setup
*And* the Prospect has a ++My Paradise customer++ with a ++Mavenir shopping cart++
*But* no ++plan++ is in the ++Mavenir shopping cart++
*And* Keep current plan is not shown
*When* the Prospect is forwarded to Plan Selection
*Then* the system retrieves the ++plan++ catalog from the Midtier
*And* the Prospect sees ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, and ++plan++ ++Atlas++
*And* each ++plan++ has a Select operation
*When* the Prospect clicks Select on ++plan++ ++{scenario}++
*Then* the system patches the ++Mavenir shopping cart++ with ++{scenario}++ through the Midtier
*And* the ++My Paradise customer++ cart is updated in session with ++{scenario}++
*And* the Prospect is forwarded to Time to pick your number
*Given* the Prospect is in Account Setup
*And* the Prospect has a ++My Paradise customer++ with a ++Mavenir shopping cart++
*Given* ++plan++ ++Essentials++ is in the ++Mavenir shopping cart++
*When* the Prospect arrives at Plan Selection from Checkout
*Then* the Prospect sees "Your current plan Essentials"
*And* Keep current plan is enabled
*And* the ++plan++ catalog is displayed
*And* each ++plan++ has a Select operation
*When* the Prospect clicks Select on ++plan++ ++Data Freedom++
*Then* the system patches the ++Mavenir shopping cart++ with ++plan++ ++Data Freedom++ through the Midtier
*And* the ++My Paradise customer++ cart is updated in session with ++plan++ ++Data Freedom++
*And* the Prospect is forwarded to Checkout


### Scenario: Select the ++plan++ already in the cart

### Background

*Given* the Prospect is in Account Setup
*And* the Prospect has a ++My Paradise customer++ with a ++Mavenir shopping cart++
*But* no ++plan++ is in the ++Mavenir shopping cart++
*And* Keep current plan is not shown
*When* the Prospect is forwarded to Plan Selection
*Then* the system retrieves the ++plan++ catalog from the Midtier
*And* the Prospect sees ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, and ++plan++ ++Atlas++
*And* each ++plan++ has a Select operation
*When* the Prospect clicks Select on ++plan++ ++{scenario}++
*Then* the system patches the ++Mavenir shopping cart++ with ++{scenario}++ through the Midtier
*And* the ++My Paradise customer++ cart is updated in session with ++{scenario}++
*And* the Prospect is forwarded to Time to pick your number
*Given* the Prospect is in Account Setup
*And* the Prospect has a ++My Paradise customer++ with a ++Mavenir shopping cart++
*Given* ++plan++ ++Essentials++ is in the ++Mavenir shopping cart++
*When* the Prospect arrives at Plan Selection from Checkout
*Then* the Prospect sees "Your current plan Essentials"
*And* Keep current plan is enabled
*And* the ++plan++ catalog is displayed
*And* each ++plan++ has a Select operation
*When* the Prospect clicks Select on ++plan++ ++Data Freedom++
*Then* the system patches the ++Mavenir shopping cart++ with ++plan++ ++Data Freedom++ through the Midtier
*And* the ++My Paradise customer++ cart is updated in session with ++plan++ ++Data Freedom++
*And* the Prospect is forwarded to Checkout
*Given* the Prospect is in Account Setup
*And* the Prospect has a ++My Paradise customer++ with a ++Mavenir shopping cart++
*Given* ++plan++ ++Essentials++ is in the ++Mavenir shopping cart++
*When* the Prospect clicks Select on ++plan++ ++Essentials++
*Then* the Prospect stays on Plan Selection to choose a different ++plan++ or Keep current plan


### Scenario: Failed to update plan

### Background

*Given* the Prospect is in Account Setup
*And* the Prospect has a ++My Paradise customer++ with a ++Mavenir shopping cart++
*But* no ++plan++ is in the ++Mavenir shopping cart++
*And* Keep current plan is not shown
*When* the Prospect is forwarded to Plan Selection
*Then* the system retrieves the ++plan++ catalog from the Midtier
*And* the Prospect sees ++plan++ ++Essentials++, ++plan++ ++Data Freedom++, ++plan++ ++Ace++, and ++plan++ ++Atlas++
*And* each ++plan++ has a Select operation
*When* the Prospect clicks Select on ++plan++ ++{scenario}++
*Then* the system patches the ++Mavenir shopping cart++ with ++{scenario}++ through the Midtier
*And* the ++My Paradise customer++ cart is updated in session with ++{scenario}++
*And* the Prospect is forwarded to Time to pick your number
*Given* the Prospect is in Account Setup
*And* the Prospect has a ++My Paradise customer++ with a ++Mavenir shopping cart++
*Given* ++plan++ ++Essentials++ is in the ++Mavenir shopping cart++
*When* the Prospect arrives at Plan Selection from Checkout
*Then* the Prospect sees "Your current plan Essentials"
*And* Keep current plan is enabled
*And* the ++plan++ catalog is displayed
*And* each ++plan++ has a Select operation
*When* the Prospect clicks Select on ++plan++ ++Data Freedom++
*Then* the system patches the ++Mavenir shopping cart++ with ++plan++ ++Data Freedom++ through the Midtier
*And* the ++My Paradise customer++ cart is updated in session with ++plan++ ++Data Freedom++
*And* the Prospect is forwarded to Checkout
*Given* the Prospect is in Account Setup
*And* the Prospect has a ++My Paradise customer++ with a ++Mavenir shopping cart++
*Given* ++plan++ ++Essentials++ is in the ++Mavenir shopping cart++
*When* the Prospect clicks Select on ++plan++ ++Essentials++
*Then* the Prospect stays on Plan Selection to choose a different ++plan++ or Keep current plan
*Given* the Prospect is in Account Setup
*And* the Prospect has a ++My Paradise customer++ with a ++Mavenir shopping cart++
*Given* Midtier PATCH to ++Mavenir shopping cart++ returns a server error
*When* the Prospect clicks Select on ++plan++ ++Data Freedom++
*Then* My Paradise shows "Failed to update new plan choice."
*And* the Prospect stays on Plan Selection
