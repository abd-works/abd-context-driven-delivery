## Story: Upgrade To Data Freedom

### Scenario: Upgrade plan from review: ${example}

*Given* ${currentPlan.name} is in the Mavenir shopping cart
*When* My Paradise patches the Mavenir shopping cart with ${newPlan.name}
*Then* My Paradise sends the patch cart request to Mavenir with ${newPlan.name} bundleId
*When* Mavenir returns the updated Mavenir shopping cart with ${newPlan.name}
*Then* My Paradise stores ${newPlan.name} as the cart bundle

### Examples

| example |
| --- |
| customerWithCart |
| reloadCart |
