## Story: Upgrade To Data Freedom

### Examples

| example | plan upgrade | currentPlan | newPlan |
| --- | --- | --- | --- |
| upgrade to Data Freedom | plan upgrade | Essentials | Data Freedom |
| upgrade to Ace | plan upgrade | Data Freedom | Ace |
| upgrade to Atlas | plan upgrade | Ace | Atlas |

### Scenario Outline: Upgrade plan from review

### Background

*Given* the Customer is reviewing their order
*And* the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++

*Given* ++plan++ ++{currentPlan}++ is in the ++Mavenir shopping cart++
*When* My Paradise patches the ++Mavenir shopping cart++ with ++plan++ ++{newPlan}++
*Then* My Paradise sends the patch cart request to Mavenir with ++plan++ ++{newPlan}++ bundleId
*When* Mavenir returns the updated ++Mavenir shopping cart++ with ++plan++ ++{newPlan}++
*Then* My Paradise stores ++plan++ ++{newPlan}++ as the cart bundle
*And* the Customer sees *You have been upgraded!*

### Scenario: No upsell shown on top-tier plan

### Background

*Given* the Customer is reviewing their order
*And* the Customer has a ++My Paradise customer++ with a ++Mavenir shopping cart++

*Given* ++plan++ ++Atlas++ is in the ++Mavenir shopping cart++
*When* the Customer proceeds to reviewing their order
*Then* no upgrade option is available
