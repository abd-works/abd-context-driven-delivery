## Story: Ensure Cart on Customer

### Scenario: Load Cart — no cart

*Given* the Customer enters the onboarding journey with a valid account token and no cart
*When* My Paradise loads the cart for the customer
*Then* My Paradise finds no cart on the customer

### Examples

| example |
| --- |
| storedAccountCredentialsWithToken |

### Scenario: Create Cart

*Given* the Customer enters the onboarding journey with a valid account token and no cart
*When* My Paradise creates a cart for the customer
*Then* My Paradise sends the create request to Midtier with the customer id
*When* Mavenir creates the shopping cart
*Then* My Paradise stores the cart on the customer
*And* the Customer proceeds to Get Number

### Examples

| example |
| --- |
| storedAccountCredentialsWithToken |

### Scenario: customer already has a Mavenir shopping cart

*Given* the Customer enters the onboarding journey with a valid account token
*And* the customer has a Mavenir shopping cart
*When* My Paradise loads the cart for the customer
*Then* My Paradise finds the cart on the customer
*And* the Customer proceeds to Get Number

### Examples

| example |
| --- |
| storedAccountCredentialsWithToken |
| newMavenirShoppingCart |

### Scenario: cart already exists

*Given* the Customer enters the onboarding journey and already has a cart loaded
*When* My Paradise creates a cart for the customer
*Then* My Paradise reports a cart creation error

### Examples

| example |
| --- |
| storedAccountCredentialsWithToken |
| newMavenirShoppingCart |
