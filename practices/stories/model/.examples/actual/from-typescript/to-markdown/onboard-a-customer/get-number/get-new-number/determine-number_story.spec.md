## Story: Determine Number

### Scenario: View available numbers

*Given* a My Paradise customer with a Mavenir shopping cart and no MSISDN
*When* the Customer loads available numbers
*Then* My Paradise sends the list resources request to Mavenir
*When* Mavenir locks 20 MSISDN resources and returns the available number values
*Then* My Paradise returns the available numbers

### Examples

| example |
| --- |
| storedHeldAvailableNumber |
| enteredChosenAvailableNumber |
| storedAvailableNumbers |
| customerWithCart |

### Scenario: View available numbers — MSISDN in cart

*When* the Customer loads available numbers
*Then* My Paradise sends the list resources request to Mavenir
*When* Mavenir locks 20 MSISDN resources and returns the available number values
*And* My Paradise returns the available numbers

### Examples

| example |
| --- |
| storedHeldAvailableNumber |
| storedAvailableNumbers |
| customerWithCart |
| stubBundle |

### Scenario: Refresh available numbers

*Given* a My Paradise customer with a Mavenir shopping cart
*When* the Customer refreshes the number list
*Then* My Paradise sends the list resources request to Mavenir
*When* Mavenir locks 20 MSISDN resources and returns the available numbers
*Then* My Paradise returns a fresh set of available numbers

### Examples

| example |
| --- |
| storedAvailableNumbers |
| customerWithCart |

### Scenario: Search for a number

*Given* a My Paradise customer with a Mavenir shopping cart
*When* the Customer searches for numbers matching JAMES (52637)
*Then* My Paradise sends the search request to Mavenir with pattern 52637
*When* Mavenir locks MSISDN resources matching 52637 and returns matching values
*Then* My Paradise returns Available Numbers matching 52637
*And* the matching numbers are stored on the line for selection

### Examples

| example |
| --- |
| customerWithCart |

### Scenario: Numbers locked by another customer are excluded from results

*Given* another customer has already locked the standard available numbers in Mavenir
*When* the Customer loads available numbers
*Then* My Paradise sends the list resources request to Mavenir
*When* Mavenir returns only available numbers, excluding the locked ones
*Then* the locked numbers are not in the available numbers list
*And* only the currently available numbers are returned

### Examples

| example |
| --- |
| storedHeldAvailableNumber |
| enteredChosenAvailableNumber |
| customerWithCart |

### Scenario: Pick number

*When* Mavenir confirms the reservation and patches the cart
*And* the Customer is forwarded to Select Sim

### Examples

| example |
| --- |
| enteredChosenAvailableNumber |
| expectedChosenAvailableNumber |
| storedAvailableNumbers |
| customerWithCart |
| reloadCart |
| stubBundle |

### Scenario: Pick number — replace existing


### Examples

| example |
| --- |
| storedHeldAvailableNumber |
| enteredChosenAvailableNumber |
| expectedChosenAvailableNumber |
| storedAvailableNumbers |
| customerWithCart |
| reloadCart |
| stubBundle |

### Scenario: Reserve number request fails

*Then* My Paradise shows Failed to reserve your number.

### Examples

| example |
| --- |
| enteredChosenAvailableNumber |
| storedAvailableNumbers |
| customerWithCart |

### Scenario: Patch cart with number fails

*Then* My Paradise shows Failed to update your cart.

### Examples

| example |
| --- |
| enteredChosenAvailableNumber |
| storedAvailableNumbers |
| customerWithCart |
