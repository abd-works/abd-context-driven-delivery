## Story: Choose a Number

### Scenario: Pick number

*Given* Mavenir has locked ${enteredChosenAvailableNumber} in the available numbers list and no MSISDN is in the cart
*When* My Paradise reserves ${enteredChosenAvailableNumber} in Mavenir and patches the shopping cart
*Then* My Paradise sends the reserve request to Mavenir with ${enteredChosenAvailableNumber}
*And* My Paradise patches the Mavenir shopping cart with ${enteredChosenAvailableNumber}
*When* Mavenir confirms the reservation and patches the cart
*Then* My Paradise stores ${expectedChosenAvailableNumber} on the line
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

*Given* MSISDN ${storedHeldAvailableNumber} is in the cart and Mavenir has locked ${enteredChosenAvailableNumber} in the available numbers list
*When* My Paradise reserves ${enteredChosenAvailableNumber} releasing ${storedHeldAvailableNumber}
*Then* My Paradise sends the reserve request to Mavenir with ${enteredChosenAvailableNumber} releasing ${storedHeldAvailableNumber}
*When* Mavenir releases ${storedHeldAvailableNumber} and reserves ${enteredChosenAvailableNumber}
*Then* My Paradise stores ${expectedChosenAvailableNumber} on the line

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

*Given* Mavenir has locked ${enteredChosenAvailableNumber} in the available numbers list but reserve returns an error
*When* My Paradise attempts to reserve ${enteredChosenAvailableNumber} but Mavenir returns an error
*Then* My Paradise shows Failed to reserve your number.

### Examples

| example |
| --- |
| enteredChosenAvailableNumber |
| storedAvailableNumbers |
| customerWithCart |

### Scenario: Patch cart with number fails

*Given* Mavenir has reserved ${enteredChosenAvailableNumber} but patching the cart returns an error
*When* My Paradise patches the Mavenir shopping cart with ${enteredChosenAvailableNumber} but Mavenir returns an error
*Then* My Paradise shows Failed to update your cart.

### Examples

| example |
| --- |
| enteredChosenAvailableNumber |
| storedAvailableNumbers |
| customerWithCart |
